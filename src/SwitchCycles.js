import React from "react";

import Button from "react-bootstrap/Button";

import { PlotData, PlotNew, usePlot } from "./BokehPlot";

import DeviceTable from "./DeviceTable";
import { LoadingAnimation } from "./Toolbar";

import { downloadFile, usePostApi } from "./Fetch";

const TableHeader = () => (
    <>
        <th>Cycles</th>
        <th>Download</th>
    </>
);

const TableRow = (props) => {
    const plot_name = "PlotOnOffCyclesCrashes";
    const plot_parameters = { device: props.device_id };
    const file_name = `system_stability_${props.device_id}.xlsx`;
    const [{ fields, isLoading, isError, errorMsg }, plot] = usePlot(plot_name, plot_parameters);

    return (
        <>
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

const SwitchCycles = () => <DeviceTable format_header={TableHeader} format_row={TableRow} />;

export default SwitchCycles;
