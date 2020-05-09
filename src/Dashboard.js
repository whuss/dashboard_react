import React, { useState, useEffect } from "react";

import Table from "react-bootstrap/Table";

import Spinner from "react-bootstrap/Spinner";

import useDataApi from "./Fetch";

import Toolbar, { useDeviceFilter } from "./Toolbar";

function DeviceTable(props) {
    const [selectedDevices, setFilterStr] = useDeviceFilter();

    return (
        <>
            <Toolbar>{setFilterStr}</Toolbar>
            <props.format_table data={selectedDevices}/>
        </>
    );
}

const loading_row = () => (
    <>
        <td>
            <Spinner animation="border" size="sm" variant="secondary" />
        </td>
        <td></td>
        <td></td>
        <td></td>
    </>
);

const format_row = (data) => (
    <>
        <td>
            <div className={`deviceMode ${data.study_mode}`}>{data.study_mode}</div>
        </td>
        <td>{data.offline_duration}</td>
        <td>
            <i className={"fa fa-heartbeat " + data.health_status}></i>
        </td>
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
};

const TableHeader = () => (
    <>
        <th>Device Mode</th>
        <th>Last Connection</th>
        <th colSpan={2}>Health Status</th>
    </>
);

const DashboardTable = (props) => {
    const [ascending, setAscenting] = useState(DashboardTable.ascending);

    function sort(d)
    {
        if (!ascending)
        {
            return d.reverse();
        }
        return d;
    }

    const devices = props.data.sort();

    useEffect(() => {
        console.log("Set sorting: ", ascending);
        DashboardTable.ascending = ascending;
    }, [ascending]);

    return (<Table className={"dataTable"} hover>
        <thead>
            <tr>
                <th id="head_device" onClick={()=> setAscenting(!ascending)}>Device</th>
                <TableHeader />
            </tr>
        </thead>
        <tbody>
            {sort(devices).map((device) => (
                <tr key={device}>
                    <th>{device}</th>
                    <DeviceState device_id={device} />
                </tr>
            ))}
        </tbody>
    </Table>);
};
DashboardTable.ascending = true;

const Dashboard = () => <DeviceTable format_table={DashboardTable} />;

export default Dashboard;
