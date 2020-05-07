import React from "react";

import Table from "react-bootstrap/Table";
import Button from "react-bootstrap/Button";

import Plot from "./BokehPlot";
import DeviceTable from "./DeviceTable";

function plotUrl(device) {
    return `/backend/plot_switch_cycle/${device}`;
}

function table(data) {
    return (
        <Table className={"dataTable"} hover>
            <thead>
                <tr>
                    <th>Device ID</th>
                    <th>Cycles</th>
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

const SwitchCycles = () => <DeviceTable format_table={table}/>;


export default SwitchCycles;
