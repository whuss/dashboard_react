import React from "react";

import Button from "react-bootstrap/Button";

import { DeviceTableNew } from "./DeviceTable";

import Plot from "./BokehPlot";

function plotUrl(device) {
    return `/backend/plot_system_stability/${device}`;
}

const TableHeader = () => (
    <>
        <th>Total crashes</th>
        <th>Total restarts</th>
        <th>Stability</th>
        <th>Download</th>
    </>
);

const TableRow = (props) => {
    return (
        <>
            <td></td>
            <td></td>
            <td>
                <Plot src={plotUrl(props.device_id)} />
            </td>
            <td>
                <Button>Download</Button>
            </td>
        </>
    );
};

const AnalyticsScenes = () => <DeviceTableNew format_header={TableHeader} format_row={TableRow} />;

export default AnalyticsScenes;
