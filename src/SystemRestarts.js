import React, { Component, useState, useEffect, useRef } from "react";

import useDataApi from "./Fetch";

import Table from "react-bootstrap/Table";
import Button from "react-bootstrap/Button";

import DeviceTable from "./DeviceTable";

import Plot from "./BokehPlot";

function plotUrl(device) {
    return `/backend/plot_system_stability/${device}`;
}

function Restarts(props) {
    const [{ data, isLoading, isError }, doFetch] = useDataApi(`/backend/system_restarts/${props.device}`, []);

    return (
        <>
            {isError && <div>Something went wrong ...</div>}
            {isLoading ? <div>Loading ...</div> : <div dangerouslySetInnerHTML={{ __html: data.table}}/>}
        </>
    );
}

function table(data) {
    return (
        <Table className={"dataTable"} hover>
            <thead>
                <tr>
                    <th>Device ID</th>
                    <th>System Start</th>
                </tr>
            </thead>
            <tbody>
                {data.map((device) => (
                    <tr key={device}>
                        <th>{device}</th>
                        <td><Restarts device={device}/></td>
                    </tr>
                ))}
            </tbody>
        </Table>
    );
}

const SystemRestarts = () => <DeviceTable format_table={table}/>;

export default SystemRestarts;
