import React from "react";

import Button from "react-bootstrap/Button";

import DeviceTable from "./DeviceTable";

import Plot from "./BokehPlot";

import { downloadFile } from "./Fetch";

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
            <Button
                    onClick={() =>
                        downloadFile("PlotCrashes", { device: props.device_id }, `system_stability_${props.device_id}.xlsx`)
                    }
                >
                    Download
                </Button>
            </td>
        </>
    );
};

const AnalyticsScenes = () => <DeviceTable format_header={TableHeader} format_row={TableRow} />;

export default AnalyticsScenes;
