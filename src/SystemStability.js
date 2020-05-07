import React, { Component, useState, useEffect, useRef } from "react";

import useDataApi from "./Fetch";

import Table from "react-bootstrap/Table";
import Button from "react-bootstrap/Button";

import DeviceTable from "./DeviceTable";

import Plot from "./BokehPlot";

function plotUrl(device) {
    return `/backend/plot_system_stability/${device}`;
}

function table(data) {
    return (
        <Table className={"dataTable"} hover>
            <thead>
                <tr>
                    <th>Device ID</th>
                    <th>Total crashes</th>
                    <th>Total restarts</th>
                    <th>Stability</th>
                    <th>Download</th>
                </tr>
            </thead>
            <tbody>
                {data.map((device) => (
                    <tr key={device}>
                        <th>{device}</th>
                        <td></td>
                        <td></td>
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

const AnalyticsScenes = () => <DeviceTable format_table={table}/>;

export default AnalyticsScenes;
