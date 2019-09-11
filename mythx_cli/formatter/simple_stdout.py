from typing import List, Union

import click
from mythx_models.response import (
    AnalysisInputResponse,
    AnalysisListResponse,
    AnalysisStatusResponse,
    DetectedIssuesResponse,
    VersionResponse,
)

from mythx_cli.formatter.base import BaseFormatter
from mythx_cli.util import get_source_location_by_offset


class SimpleFormatter(BaseFormatter):
    @staticmethod
    def format_analysis_list(resp: AnalysisListResponse) -> str:
        res = []
        for analysis in resp:
            res.append("UUID: {}".format(analysis.uuid))
            res.append("Submitted at: {}".format(analysis.submitted_at))
            res.append("Status: {}".format(analysis.status))
            res.append("")

        return "\n".join(res)

    @staticmethod
    def format_analysis_status(resp: AnalysisStatusResponse) -> str:
        res = [
            "UUID: {}".format(resp.uuid),
            "Submitted at: {}".format(resp.submitted_at),
            "Status: {}".format(resp.status),
            "",
        ]
        return "\n".join(res)

    @staticmethod
    def format_detected_issues(
        resp: DetectedIssuesResponse, inp: AnalysisInputResponse
    ) -> str:
        res = []
        ctx = click.get_current_context()
        # TODO: Sort by file
        for report in resp.issue_reports:
            for issue in report.issues:
                res.append("UUID: {}".format(ctx.obj["uuid"]))
                res.append(
                    "Title: {} ({})".format(issue.swc_title or "-", issue.severity)
                )
                res.append("Description: {}".format(issue.description_long))
                res.append("")

                for loc in issue.locations:
                    comp = loc.source_map.components[0]
                    source_list = loc.source_list or report.source_list
                    if source_list and 0 >= comp.file_id < len(source_list):
                        filename = source_list[comp.file_id]
                        if filename not in inp.sources:
                            # Skip files we don't have source for (e.g. with unresolved bytecode hashes)
                            res.append("")
                            continue
                        line = get_source_location_by_offset(
                            inp.sources[filename]["source"], comp.offset
                        )
                        snippet = inp.sources[filename]["source"].split("\n")[line - 1]
                        res.append("{}:{}".format(filename, line))
                        res.append(snippet)

                    res.append("")

        return "\n".join(res)

    @staticmethod
    def format_version(resp: VersionResponse) -> str:
        return "\n".join(
            [
                "API: {}".format(resp.api_version),
                "Harvey: {}".format(resp.harvey_version),
                "Maru: {}".format(resp.maru_version),
                "Mythril: {}".format(resp.mythril_version),
                "Hashed: {}".format(resp.hashed_version),
            ]
        )
