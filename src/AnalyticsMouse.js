import React from "react";

import Button from "react-bootstrap/Button";

import Plot from "./BokehPlot";
import { DeviceTableNew } from "./DeviceTable";

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
                <Button>Download</Button>
            </td>
        </>
    );
};

const AnalyticsMouse = () => <DeviceTableNew format_header={TableHeader} format_row={TableRow} />;

export default AnalyticsMouse;
