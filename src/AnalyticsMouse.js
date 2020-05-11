import React from "react";

import Button from "react-bootstrap/Button";

import Plot from "./BokehPlot";
import DeviceTable from "./DeviceTable";

import { downloadFile } from "./Fetch";

function plotUrl(device) {
    return `/backend/plot_analytics_mouse/${device}`;
}

const TableHeader = () => (
    <>
        <th>Mouse data</th>
        <th>Download</th>
    </>
);

const TableRow = (props) => {
    return (
        <>
            <td>
                <Plot src={plotUrl(props.device_id)} />
            </td>
            <td>
                <Button onClick={() => downloadFile('PlotMouse', {device: props.device_id}, `analytics_mouse_${props.device_id}.xlsx`)}>Download</Button>
            </td>
        </>
    );
};

const AnalyticsMouse = () => <DeviceTable format_header={TableHeader} format_row={TableRow} />;

export default AnalyticsMouse;
