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
    const plot_name = "PlotCrashes";
    const plot_parameters = { device: props.device_id };
    const file_name = `system_stability_${props.device_id}.xlsx`;
    const [{ fields, isLoading, isError, errorMsg }, plot] = usePlot(plot_name, plot_parameters);

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
                {!isLoading && !isError && (
                    <Button onClick={() => downloadFile(plot_name, plot_parameters, file_name)}>Download</Button>
                )}
            </td>
        </>
    );
};

const AnalyticsScenes = () => <DeviceTable format_header={TableHeader} format_row={TableRow} />;

export default AnalyticsScenes;
