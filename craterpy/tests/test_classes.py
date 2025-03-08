"""Unittest classes.py."""

import warnings
from pathlib import Path
import unittest
import pyproj
import pandas as pd
import shapely
from shapely.testing import assert_geometries_equal
from shapely.geometry import Point
import craterpy
from craterpy.classes import CraterDatabase, CRS_DICT


class TestCraterDatabase(unittest.TestCase):
    """TestCraterDatabase class."""

    def setUp(self):
        data_dir = Path(craterpy.__path__[0], "data")
        self.moon_tif = data_dir / "moon.tif"
        self.crater_list = data_dir / "craters.csv"

    def test_add_annuli(self):
        """Test adding annular shapefiles to CraterDataBase."""
        cdb = CraterDatabase(self.crater_list)
        cdb.add_annuli(1, 2, "ejecta")
        # Check that ejecta appears in the string repr
        self.assertIn("ejecta", str(cdb))
        # Test that ejecta was registered as a propety and contains a shapely geom
        self.assertIsInstance(cdb.ejecta[0], shapely.geometry.Polygon)

    def test_annuli_precision(self):
        """Test that simple and precise annuli mostly agree."""
        cdb = CraterDatabase(self.crater_list)
        cdb.add_annuli(0, 1, "precise", precise=True)
        cdb.add_annuli(0, 1, "simple", precise=False)
        assert_geometries_equal(cdb.precise, cdb.simple, tolerance=1)

    def test_get_stats(self):
        """Test getting statistics on a region for a raster."""
        cdb = CraterDatabase(self.crater_list)
        cdb.add_annuli(1, 1.1, "rim")
        stats = cdb.get_stats(self.moon_tif, "rim", ["count"])
        self.assertIn("count_rim", stats.columns)

    def test_get_stats_parallel(self):
        """Test parallellization of get_stats for multiple rasters/regions."""
        pass

    def test_plot(self):
        """Test CraterDatabase summary plot."""
        # Create a minimal DataFrame
        df = pd.DataFrame({
            "lat": [0.0, 10.0],
            "lon": [0.0, 20.0],
            "radius": [1.0, 2.0]
        })
        cdb = CraterDatabase(df)
        cdb.add_annuli(0, 1, "test_annulus")
        # Generate the plot.
        ax = cdb.plot()
        self.assertIsNotNone(ax)
        from matplotlib.axes import Axes
        self.assertIsInstance(ax, Axes)

    def test_body_crs_all(self):
        """Test that every defined CRS loads."""
        for body in CRS_DICT.keys():
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", message="Vesta*")
                cdb = CraterDatabase(self.crater_list, body)
                for crs in [
                    v for k, v in cdb.__dict__.items() if k.startswith("_crs")
                ]:
                    self.assertIsInstance(crs, pyproj.CRS)

    def test_vesta_coord_correction(self):
        """Test Vesta's various coordinate systems."""
        pass

    def test_import_dataframe(self):
        """Test importing from a dataframe."""
        # Create a minimal DataFrame with crater data.
        df = pd.DataFrame({
            "lat": [0.0, 10.0],
            "lon": [0.0, 20.0],
            "radius": [1.0, 2.0]
        })
        cdb = CraterDatabase(df)
        self.assertTrue(hasattr(cdb.data, "geometry"))
        self.assertEqual(len(cdb.data), 2)
        self.assertIsInstance(cdb.data.geometry.iloc[0], Point)
        self.assertAlmostEqual(cdb.data.geometry.iloc[0].x, 0.0)
        self.assertAlmostEqual(cdb.data.geometry.iloc[0].y, 0.0)

    def test_units(self):
        """Test importing with radii in m or km."""
        df_km = pd.DataFrame({"lat": [0.0], "lon": [0.0], "radius": [1.0]})
        cdb_km = CraterDatabase(df_km, units="km")
        # Expecting radius to be converted to meters
        self.assertAlmostEqual(cdb_km.rad.iloc[0], 1000.0)

        df_m = pd.DataFrame({"lat": [0.0], "lon": [0.0], "radius": [1000.0]})
        cdb_m = CraterDatabase(df_m, units="m")
        self.assertAlmostEqual(cdb_m.rad.iloc[0], 1000.0)

    def test_rad_vs_diam(self):
        """Test importing with radii and diam columns."""
        # Create a DataFrame with a diameter column instead of radius.
        
        # Diameter in meters; expecting radius = 5 m.
        df = pd.DataFrame({"lat": [0.0], "lon": [0.0], "diameter": [10.0]})
        cdb = CraterDatabase(df, units="m")
        self.assertAlmostEqual(cdb.rad.iloc[0], 5.0)
        df = pd.DataFrame({"lat": [0.0], "lon": [0.0], "diam": [10.0]})
        cdb = CraterDatabase(df, units="m")
        self.assertAlmostEqual(cdb.rad.iloc[0], 5.0)

        df = pd.DataFrame({"lat": [0.0], "lon": [0.0], "radius": [10.0]})
        cdb = CraterDatabase(df, units="m")
        self.assertAlmostEqual(cdb.rad.iloc[0], 10.0)
        df = pd.DataFrame({"lat": [0.0], "lon": [0.0], "radii": [10.0]})
        cdb = CraterDatabase(df, units="m")
        self.assertAlmostEqual(cdb.rad.iloc[0], 10.0)

    def test_gen_annulus_simple(self):
        """Test generating simple annuli."""
        pass

    def test_gen_annulus_precise(self):
        """Test generating precise annuli."""
        pass

    def test_antimeridian_splitting(self):
        """Test generating annuli when split over the antimeridian."""
        pass

    def test_pole_crossing(self):
        """Test annuli that cross the North or South pole."""
        pass
