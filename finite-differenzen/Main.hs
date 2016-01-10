{-# LANGUAGE TupleSections, GeneralizedNewtypeDeriving, DeriveFunctor #-}
module Main where

import Data.List
import Data.Ratio
import Control.Exception
import Control.Arrow ((***))

type R   = Double
type Nat = Int
type Ix  = Int

data Loc = Boundary | Inner deriving (Show,Eq)

newtype D1 a = MkD1 { unD1 :: a } deriving (Show,Eq,Num)
newtype D2 a = MkD2 { unD2 :: (a,a) } deriving (Show,Eq)

data Mesh f = MkMesh
    { width  :: R
    , size   :: Nat  -- total number of parameters
    , ix     :: f Ix -> Ix
    , pos    :: f Ix -> f R
    , points :: [(Loc, f Ix)]
    }

innerPoints :: Mesh f -> [f Ix]
innerPoints = map snd . filter ((== Inner) . fst) . points

boundaryPoints :: Mesh f -> [f Ix]
boundaryPoints = map snd . filter ((== Boundary) . fst) . points

data Mat a = MkMat
    { numRows :: Int
    , numCols :: Int
    , entries :: [(Ix, Ix, a)]
    } deriving (Show,Functor)

dx :: Mesh D1 -> Mat R
dx mesh = collect (size mesh) $ for (innerPoints mesh) $ \p ->
    [ (ix mesh (p + 1),  1 / (2 * h))
    , (ix mesh (p - 1), -1 / (2 * h))
    ]
    where h = width mesh

laplace :: Mesh D2 -> Mat R
laplace mesh = collect (size mesh) $ for (innerPoints mesh) $ \p ->
    [ (ix mesh p,                    -4 / h^2)
    , (ix mesh (p <+> MkD2 (-1, 0)),  1 / h^2)
    , (ix mesh (p <+> MkD2 ( 0,-1)),  1 / h^2)
    , (ix mesh (p <+> MkD2 ( 1,0)),   1 / h^2)
    , (ix mesh (p <+> MkD2 ( 0,1)),   1 / h^2)
    ]
    where h = width mesh

dirichlet :: Mesh f -> Mat R
dirichlet mesh = collect (size mesh) $ for (boundaryPoints mesh) $ \p ->
    [ (ix mesh p, 1)
    ]

heat1 :: (R -> R) -> (R -> R) -> Mesh D1 -> (Mat R,Mat R)
heat1 u0 f mesh =
    ( fmap negate (dx mesh) <==> dirichlet mesh
    , evalInner (\p -> f (unD1 p)) mesh <==> evalBoundary (\p -> u0 (unD1 p)) mesh
    )

heat2 :: ((R,R) -> R) -> ((R,R) -> R) -> Mesh D2 -> (Mat R,Mat R)
heat2 u0 f mesh =
    ( fmap negate (laplace mesh) <==> dirichlet mesh
    , evalInner (\p -> f (unD2 p)) mesh <==> evalBoundary (\p -> u0 (unD2 p)) mesh
    )

mkMesh1 :: Rational -> Rational -> Mesh D1
mkMesh1 len h = MkMesh
    { width  = fromRational h
    , size   = n
    , ix     = \(MkD1 i) -> i
    , pos    = \(MkD1 i) -> MkD1 $ fromIntegral i * fromRational h
    , points = map (id *** MkD1) $ [(Boundary, 0)] ++ map (Inner,) [1..n-2] ++ [(Boundary, n-1)]
    }
    where n = maybe (error "Total length must be a multiple of the mesh width") succ $ toInt (len / h)

mkMesh2 :: Rational -> Rational -> Mesh D2
mkMesh2 len h = MkMesh
    { width  = fromRational h
    , size   = n^2
    , ix     = \(MkD2 (i,j)) -> i*n + j
    , pos    = \(MkD2 (i,j)) -> MkD2 (fromIntegral i * fromRational h, fromIntegral j * fromRational h)
    , points = do
        i <- [0..n-1]
        j <- [0..n-1]
        return (if i == 0 || i == n-1 || j == 0 || j == n-1 then Boundary else Inner, MkD2 (i,j))
    }
    where n = maybe (error "Total length must be a multiple of the mesh width") succ $ toInt (len / h)

dummy :: (Mat R,Mat R) -> String
dummy (a,b) = "a=" ++ pythonMat a ++ ";b=np.array(" ++ pythonList (map (\(i,j,a) -> a) $ entries b) ++ ")"
-- writeFile "/tmp/foo.txt" $ dummy $ heat2 (\(x,y) -> if 0.2 <= x && x <= 0.4 then 1 else 0) (\(x,y) -> if abs (x-0.7) <= 0.2 && abs (y-0.5) <= 0.15 then 10 else 0) $ mkMesh2 1 0.05

for :: [a] -> (a -> b) -> [b]
for = flip map

collect :: Int -> [[(Ix, a)]] -> Mat a
collect n rows = assert (all ((< n) . fst) (concat rows)) $ MkMat
    { entries = concatMap (\(i,row) -> map (\(j,a) -> (i,j,a)) row) $ zip [0..] rows
    , numRows = length rows
    , numCols = n
    }

collectColumn :: [a] -> Mat a
collectColumn = collect 1 . map (\a -> [(0,a)])

eval1 :: (Loc -> f R -> a) -> Mesh f -> Mat a
eval1 f mesh = collectColumn $ for (points mesh) $ \(loc,p) -> f loc (pos mesh p)

evalInner :: (f R -> a) -> Mesh f -> Mat a
evalInner f mesh = collectColumn $ for (innerPoints mesh) $ \p -> f (pos mesh p)

evalBoundary :: (f R -> a) -> Mesh f -> Mat a
evalBoundary f mesh = collectColumn $ for (boundaryPoints mesh) $ \p -> f (pos mesh p)

infixl 6 <==>
infixl 6 <||>

(<==>) :: Mat a -> Mat a -> Mat a
(<==>) (MkMat n m ent) (MkMat n' m' ent') = assert (m == m') $
    MkMat (n + n') m $ ent ++ map (\(i,j,a) -> (n+i,j,a)) ent'

(<||>) :: Mat a -> Mat a -> Mat a
(<||>) (MkMat n m ent) (MkMat n' m' ent') = assert (n == n') $
    MkMat n (m + m') $ ent ++ map (\(i,j,a) -> (i,m+j,a)) ent'

class Vec a where
    infixl 6 <+>
    (<+>) :: a -> a -> a

instance (Num a) => Vec (D1 a) where
    MkD1 x <+> MkD1 x' = MkD1 (x + x')

instance (Num a) => Vec (D2 a) where
    MkD2 (x,y) <+> MkD2 (x',y') = MkD2 (x+x', y+y')

toInt :: Rational -> Maybe Int
toInt x
    | denominator x == 1 = Just $ fromIntegral $ numerator x
    | otherwise          = Nothing

pythonMat :: (Show a) => Mat a -> String
pythonMat (MkMat n m ent) = concat
    [ "csr_matrix(("
    , pythonList (map (\(i,j,a) -> a) ent)
    , ", ("
    , pythonList (map (\(i,j,a) -> i) ent)
    , ", "
    , pythonList (map (\(i,j,a) -> j) ent)
    , ")), shape=(" ++ show n ++ "," ++ show m ++ "))"
    ]

pythonList :: (Show a) => [a] -> String
pythonList = show
