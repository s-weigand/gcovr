# -*- coding:utf-8 -*-

#  ************************** Copyrights and license ***************************
#
# This file is part of gcovr 6.0+master, a parsing and reporting tool for gcov.
# https://gcovr.com/en/stable
#
# _____________________________________________________________________________
#
# Copyright (c) 2013-2023 the gcovr authors
# Copyright (c) 2013 Sandia Corporation.
# Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
# the U.S. Government retains certain rights in this software.
#
# This software is distributed under the 3-clause BSD License.
# For more information, see the README.rst file.
#
# ****************************************************************************

from typing import List

from ...options import GcovrConfigOption, OutputOrDefault
from ...formats.base import BaseHandler

from ...coverage import CovData


class CoberturaHandler(BaseHandler):
    def get_options() -> List[GcovrConfigOption]:
        return [
            GcovrConfigOption(
                "cobertura",
                ["--cobertura", "-x", "--xml"],
                group="output_options",
                metavar="OUTPUT",
                help=(
                    "Generate a Cobertura XML report. "
                    "OUTPUT is optional and defaults to --output."
                ),
                nargs="?",
                type=OutputOrDefault,
                default=None,
                const=OutputOrDefault(None),
            ),
            GcovrConfigOption(
                "cobertura_pretty",
                ["--cobertura-pretty", "--xml-pretty"],
                group="output_options",
                help=(
                    "Pretty-print the Cobertura XML report. "
                    "Implies --cobertura. Default: {default!s}."
                ),
                action="store_true",
            ),
        ]

    def write_report(self, covdata: CovData, output_file: str) -> None:
        from .write import write_report

        write_report(covdata, output_file, self.options)
