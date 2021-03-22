import hepdata_lib
import json
from collections import OrderedDict as od
import re
import sys

from hepdata_lib import Submission
submission = Submission()

# Make table of results
from data.results_mu import *
table_mu = make_table()
from data.correlations_mu import *
table_correlations_mu = make_table()

from data.results_stage1p2_maximal import *
table_maximal = make_table()
from data.correlations_stage1p2_maximal import *
table_correlations_stage1p2_maximal = make_table()

from data.results_stage1p2_minimal import *
table_minimal = make_table()
from data.correlations_stage1p2_minimal import *
table_correlations_stage1p2_minimal = make_table()

from data.results_kappas import *
table_kappas = make_table()
from data.results_kappas_expected import *
table_kappas_expected = make_table()
from data.results_kVkF import *
table_kVkF = make_table()
from data.results_kVkF_expected import *
table_kVkF_expected = make_table()



from data.results_stage0 import *
table_stage0 = make_table()
from data.correlations_stage0 import *
table_correlations_stage0 = make_table()

from data.results_stage1p2_maximal_2d_vbflike import *
table_stage1p2_maximal_2d_vbflike = make_table()
from data.results_stage1p2_maximal_2d_vbflike_exp import *
table_stage1p2_maximal_2d_vbflike_expected = make_table()
from data.results_stage1p2_maximal_2d_top import *
table_stage1p2_maximal_2d_top = make_table()
from data.results_stage1p2_maximal_2d_top_exp import *
table_stage1p2_maximal_2d_top_expected = make_table()



# Add table to submission
submission.add_table(table_mu)
submission.add_table(table_correlations_mu)

submission.add_table(table_maximal)
submission.add_table(table_correlations_stage1p2_maximal)

submission.add_table(table_minimal)
submission.add_table(table_correlations_stage1p2_minimal)

submission.add_table(table_kappas)
submission.add_table(table_kappas_expected)
submission.add_table(table_kVkF)
submission.add_table(table_kVkF_expected)

submission.add_table(table_stage0)
submission.add_table(table_correlations_stage0)

submission.add_table(table_stage1p2_maximal_2d_vbflike)
submission.add_table(table_stage1p2_maximal_2d_vbflike_expected)
submission.add_table(table_stage1p2_maximal_2d_top)
submission.add_table(table_stage1p2_maximal_2d_top_expected)

# Add general table info
for table in submission.tables:
  table.keywords["cmenergies"] = [13000]

# Output
outdir = "output"
submission.create_files(outdir)
