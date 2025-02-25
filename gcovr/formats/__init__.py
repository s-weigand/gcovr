import logging
from typing import Callable, List, Optional, Tuple

from ..options import GcovrConfigOption, Options

from ..coverage import CovData

# the handler
from .gcov import GcovHandler
from .cobertura import CoberturaHandler
from .html import HtmlHandler
from .json import JsonHandler
from .txt import TxtHandler
from .csv import CsvHandler
from .sonarqube import SonarqubeHandler
from .coveralls import CoverallsHandler

LOGGER = logging.getLogger("gcovr")


def get_options() -> List[GcovrConfigOption]:
    return [
        o
        for o in [
            *GcovHandler.get_options(),
            *TxtHandler.get_options(),
            *CoberturaHandler.get_options(),
            *HtmlHandler.get_options(),
            *JsonHandler.get_options(),
            *CsvHandler.get_options(),
            *SonarqubeHandler.get_options(),
            *CoverallsHandler.get_options(),
        ]
        if not isinstance(o, str)
    ]


def read_reports(options) -> CovData:
    covdata: CovData = JsonHandler(options).read_report()

    if covdata is None:
        covdata = GcovHandler(options).read_report()

    return covdata


def write_reports(covdata: CovData, options: Options):
    from ..configuration import OutputOrDefault

    Generator = Tuple[
        List[Optional[OutputOrDefault]],
        Callable[[CovData, str], bool],
        Callable[[], None],
    ]
    generators: List[Generator] = []

    if options.txt:
        generators.append(
            (
                [options.txt],
                TxtHandler(options).write_report,
                lambda: LOGGER.warning(
                    "Text output skipped - "
                    "consider providing an output file with `--txt=OUTPUT`."
                ),
            )
        )

    if options.cobertura or options.cobertura_pretty:
        generators.append(
            (
                [options.cobertura],
                CoberturaHandler(options).write_report,
                lambda: LOGGER.warning(
                    "Cobertura output skipped - "
                    "consider providing an output file with `--cobertura=OUTPUT`."
                ),
            )
        )

    if options.html or options.html_details or options.html_nested:
        generators.append(
            (
                [options.html, options.html_details, options.html_nested],
                HtmlHandler(options).write_report,
                lambda: LOGGER.warning(
                    "HTML output skipped - "
                    "consider providing an output file with `--html=OUTPUT`."
                ),
            )
        )

    if options.sonarqube:
        generators.append(
            (
                [options.sonarqube],
                SonarqubeHandler(options).write_report,
                lambda: LOGGER.warning(
                    "Sonarqube output skipped - "
                    "consider providing an output file with `--sonarqube=OUTPUT`."
                ),
            )
        )

    if options.json or options.json_pretty:
        generators.append(
            (
                [options.json],
                JsonHandler(options).write_report,
                lambda: LOGGER.warning(
                    "JSON output skipped - "
                    "consider providing an output file with `--json=OUTPUT`."
                ),
            )
        )

    if options.json_summary or options.json_summary_pretty:
        generators.append(
            (
                [options.json_summary],
                JsonHandler(options).write_summary_report,
                lambda: LOGGER.warning(
                    "JSON summary output skipped - "
                    "consider providing an output file with `--json-summary=OUTPUT`."
                ),
            )
        )

    if options.csv:
        generators.append(
            (
                [options.csv],
                CsvHandler(options).write_report,
                lambda: LOGGER.warning(
                    "CSV output skipped - "
                    "consider providing an output file with `--csv=OUTPUT`."
                ),
            )
        )

    if options.coveralls or options.coveralls_pretty:
        generators.append(
            (
                [options.coveralls],
                CoverallsHandler(options).write_report,
                lambda: LOGGER.warning(
                    "Coveralls output skipped - "
                    "consider providing an output file with `--coveralls=OUTPUT`."
                ),
            )
        )

    writer_errors = []
    reports_were_written = False
    default_output_used = False
    default_output = OutputOrDefault(None) if options.output is None else options.output

    for output_choices, format_writer, on_no_output in generators:
        output = OutputOrDefault.choose(output_choices, default=default_output)
        if output is not None and output is default_output:
            default_output_used = True
            if not output.is_dir:
                default_output = None
        if output is not None:
            try:
                format_writer(covdata, output.abspath)
            except RuntimeError as e:
                writer_errors.append(str(e))
            reports_were_written = True
        else:
            on_no_output()

    if not reports_were_written:
        output_path = "-" if default_output is None else default_output.abspath
        default_output = None
        try:
            TxtHandler(options).write_report(covdata, output_path)
        except RuntimeError as e:
            writer_errors.append(str(e))

    if (
        default_output is not None
        and default_output.value is not None
        and not default_output_used
    ):
        LOGGER.warning(
            f"--output={repr(default_output.value)} option was provided but not used."
        )

    if options.txt_summary:
        try:
            TxtHandler(options).write_summary_report(covdata, "-")
        except RuntimeError as e:
            writer_errors.append(str(e))

    if writer_errors:
        errors_as_string = "\n".join(writer_errors)
        raise RuntimeError(
            f"Not all output files where written successful:\n{errors_as_string}"
        )
