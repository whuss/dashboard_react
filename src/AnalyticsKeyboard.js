import React from "react";

import Button from "react-bootstrap/Button";

import Plot from "./BokehPlot";
import DeviceTable from "./DeviceTable";
import { downloadFile } from "./Fetch";

function plotUrl(device) {
    return `/backend/plot_analytics_keyboard/${device}`;
}

function downloadUrl(device) {
    return `/backend/download_analytics_keyboard/${device}`;
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
                <Button onClick={() => downloadFile(downloadUrl(props.device_id), `analytics_keyboard_${props.device_id}.xlsx`)}>Download</Button>
            </td>
        </>
    );
};

const AnalyticsKeyboard = () => <DeviceTable format_header={TableHeader} format_row={TableRow} />;

export default AnalyticsKeyboard;
