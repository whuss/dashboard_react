import React from "react";

import Table from "react-bootstrap/Table";

import useDataApi from "./Fetch";
import DeviceTable from "./DeviceTable";

const loading_row = () => (
    <>
        <td></td>
        <td>Loading ...</td>
        <td></td>
        <td></td>
    </>
);

const format_row = (data) => (
    <>
        <td>{data.study_mode}</td>
        <td>{data.offline_duration}</td>
        <td>{data.health_status}</td>
        <td>{data.sick_reason}</td>
    </>
);

const DeviceState = (props) => {
    const [{ data, isLoading, isError }, doFetch] = useDataApi(`/backend/device_state/${props.device_id}`, {});

    return (
        <>
            {isError && <div>Something went wrong ...</div>}
            {isLoading ? loading_row() : format_row(data)}
        </>
    );
}

const table = (data) => (
    <Table className={"dataTable"} hover>
        <thead>
            <tr>
                <th>Device</th>
                <th>Device Mode</th>
                <th>Last Connection</th>
                <th colSpan={2}>Health Status</th>
            </tr>
        </thead>
        <tbody>
            {data.map((device) => (
                <tr key={device}>
                    <th>{device}</th>
                    <DeviceState device_id={device} />
                </tr>
            ))}
        </tbody>
    </Table>
);

const Dashboard = () => <DeviceTable format_table={table} />;

export default Dashboard;
