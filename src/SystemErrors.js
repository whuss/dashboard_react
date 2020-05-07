import React, { Component, useState, useEffect, useRef } from "react";

import useDataApi from "./Fetch";

import Table from "react-bootstrap/Table";
import Button from "react-bootstrap/Button";

import DeviceTable from "./DeviceTable";

import Plot from "./BokehPlot";

function plotUrl(device) {
    return `/backend/plot_system_errors/${device}`;
}

function table(data) {
    return (
        <Table className={"dataTable"} hover>
            <thead>
                <tr>
                    <th>Device ID</th>
                    <th>Total errors</th>
                    <th>Error locations</th>
                    <th>Download</th>
                </tr>
            </thead>
            <tbody>
                {data.map((device) => (
                    <tr key={device}>
                        <th>{device}</th>
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

const SystemErrors = () => <DeviceTable format_table={table}/>;

export default SystemErrors;
