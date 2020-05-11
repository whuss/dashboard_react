import React from "react";

import Button from "react-bootstrap/Button";

import DeviceTable from "./DeviceTable";

import Plot from "./BokehPlot";

import { downloadFile } from "./Fetch";

function plotUrl(device) {
    return `/backend/plot_system_errors/${device}`;
}

const TableHeader = () => (
    <>
        <th>Total errors</th>
        <th>Error locations</th>
        <th>Download</th>
    </>
);

const TableRow = (props) => {
    return (
        <>
            <td></td>
            <td>
                <Plot src={plotUrl(props.device_id)} />
            </td>
            <td>
                <Button
                    onClick={() =>
                        downloadFile("PlotErrors", { device: props.device_id }, `system_errors_${props.device_id}.xlsx`)
                    }
                >
                    Download
                </Button>
            </td>
        </>
    );
};

const SystemErrors = () => <DeviceTable format_header={TableHeader} format_row={TableRow} />;

export default SystemErrors;
