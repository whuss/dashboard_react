import React from "react";

import Button from "react-bootstrap/Button";

import { PlotNew } from "./BokehPlot";

import DeviceTable from "./DeviceTable";

import { downloadFile } from "./Fetch";

const TableHeader = () => (
    <>
        <th>Cycles</th>
        <th>Download</th>
    </>
);

const TableRow = (props) => {
    return (
        <>
            <td>
                <PlotNew plot_name='PlotOnOffCycles' plot_parameters={{device: props.device_id}} />
            </td>
            <td>
                <Button onClick={() => downloadFile('PlotOnOffCycles', {device: props.device_id}, `analytics_scenes_${props.device_id}.xlsx`)}>Download</Button>
            </td>
        </>
    );
}

const SwitchCycles = () => <DeviceTable format_header={TableHeader} format_row={TableRow} />;


export default SwitchCycles;
