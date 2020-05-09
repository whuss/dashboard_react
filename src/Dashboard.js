import React, { useState, useEffect } from "react";

import Table from "react-bootstrap/Table";

import Spinner from "react-bootstrap/Spinner";

import useDataApi from "./Fetch";

import Toolbar, { useDeviceFilter } from "./Toolbar";

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSortDown, faSortUp } from '@fortawesome/free-solid-svg-icons'

function DeviceTable(props) {
    const [selectedDevices, setFilterStr] = useDeviceFilter();

    return (
        <>
            <Toolbar>{setFilterStr}</Toolbar>
            <DrawTable devices={selectedDevices} format_header={props.format_header} format_row={props.format_row} />
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

const TableRow = (props) => {
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

const DrawTable = (props) => {
    const [ascending, setAscenting] = useState(DrawTable.ascending);

    function sort(d)
    {
        if (!ascending)
        {
            return d.reverse();
        }
        return d;
    }

    const SortIcon = () => {
        if (ascending)
        {
            return <FontAwesomeIcon icon={faSortDown} />;
        }
        return <FontAwesomeIcon icon={faSortUp} />
    }

    const devices = props.devices.sort();

    useEffect(() => {
        console.log("Set sorting: ", ascending);
        DrawTable.ascending = ascending;
    }, [ascending]);

    return (<Table className={"dataTable"} hover>
        <thead>
            <tr>
                <th id="head_device" onClick={()=> setAscenting(!ascending)}>Device <SortIcon/></th>
                <props.format_header />
            </tr>
        </thead>
        <tbody>
            {sort(devices).map((device) => (
                <tr key={device}>
                    <th>{device}</th>
                    <props.format_row device_id={device} />
                </tr>
            ))}
        </tbody>
    </Table>);
};
DrawTable.ascending = true;

const Dashboard = () => <DeviceTable format_header={TableHeader} format_row={TableRow}/>;

export default Dashboard;
