import React from "react";

import Button from "react-bootstrap/Button";

import DeviceTable from "./DeviceTable";

import { usePlot } from "./BokehPlot";
import { LoadingAnimation } from "./Toolbar";

import { downloadFile } from "./Fetch";

const TableHeader = () => (
    <>
        <th>Total crashes</th>
        <th>Total restarts</th>
        <th>Stability</th>
        <th>Download</th>
    </>
);

const TableRow = (props) => {
    const [{ fields, isLoading, isError, errorMsg }, plot] = usePlot("PlotCrashes", { device: props.device_id });

    return (
        <>
            <td>{fields && fields.total_number_of_crashes}</td>
            <td>{fields && fields.total_number_of_restarts}</td>
            <td>
                <LoadingAnimation isLoading={isLoading} isError={isError} errorMsg={errorMsg}>
                    {plot}
                </LoadingAnimation>
            </td>
            <td>
                <Button
                    onClick={() =>
                        downloadFile(
                            "PlotCrashes",
                            { device: props.device_id },
                            `system_stability_${props.device_id}.xlsx`
                        )
                    }
                >
                    Download
                </Button>
            </td>
        </>
    );
};

const AnalyticsScenes = () => <DeviceTable format_header={TableHeader} format_row={TableRow} />;

export default AnalyticsScenes;
