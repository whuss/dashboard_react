import React from "react";

import Button from "react-bootstrap/Button";

import Plot from "./BokehPlot";
import { DeviceTableNew } from "./DeviceTable";

function plotUrl(device) {
    return `/backend/plot_analytics_keypress/${device}`;
}

const TableHeader = () => (
    <>
        <th>Keyboard data</th>
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

const AnalyticsKeypress = () => <DeviceTableNew format_header={TableHeader} format_row={TableRow} />;

export default AnalyticsKeypress;
