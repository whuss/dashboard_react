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
    const[{ data, isLoading, isError, errorMsg }, plot] = usePlot('PlotOnOffCycles', {device: props.device_id});

    return (
        <>
            <td>
                <LoadingAnimation isLoading={isLoading} isError={isError} errorMsg={errorMsg}>{plot}</LoadingAnimation>
            </td>
            <td>
                <Button onClick={() => downloadFile('PlotOnOffCycles', {device: props.device_id}, `analytics_scenes_${props.device_id}.xlsx`)}>Download</Button>
            </td>
        </>
    );
}

const SwitchCycles = () => <DeviceTable format_header={TableHeader} format_row={TableRow} />;


export default SwitchCycles;
