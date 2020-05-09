import React, { Component, useState, useEffect, useRef } from "react";

import useDataApi from "./Fetch";

import Table from "react-bootstrap/Table";

import Spinner from "react-bootstrap/Spinner";

import { DeviceTableNew } from "./DeviceTable";

function Restarts(props) {
    const [{ data, isLoading, isError }, doFetch] = useDataApi(`/backend/system_restarts/${props.device}`, []);

    return (
        <>
            {isError && <div>Something went wrong ...</div>}
            {isLoading ? <Spinner animation="border" size="sm" variant="secondary" /> : <div dangerouslySetInnerHTML={{ __html: data.table}}/>}
        </>
    );
}

const TableHeader = () => (
    <>
        <th>System Start</th>
    </>
);

const TableRow = (props) => {
    return (
        <>
            <td><Restarts device={props.device_id}/></td>
        </>
    );
};

const SystemRestarts = () => <DeviceTableNew format_header={TableHeader} format_row={TableRow} />;

export default SystemRestarts;
