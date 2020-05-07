import React from "react";

import Table from "react-bootstrap/Table";
import Button from "react-bootstrap/Button";

import Plot from "./BokehPlot";
import DeviceTable from "./DeviceTable";

function plotUrl(device) {
    return `/backend/plot_analytics_mouse/${device}`;
}

function table(data) {
    return (
        <Table className={"dataTable"} hover>
            <thead>
                <tr>
                    <th>Device ID</th>
                    <th>Keyboard data</th>
                    <th>Download</th>
                </tr>
            </thead>
            <tbody>
                {data.map((device) => (
                    <tr key={device}>
                        <th>{device}</th>
                        <td>
                            <Plot src={plotUrl(device)} />
                        </td>
                        <td>
                            <Button>Download</Button>
                        </td>
                    </tr>
                ))}
            </tbody>
        </Table>
    );
}

const AnalyticsMouse = () => <DeviceTable format_table={table} />;

export default AnalyticsMouse;
