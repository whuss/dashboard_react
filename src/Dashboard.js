import React from "react";

import Spinner from "react-bootstrap/Spinner";

import DeviceTable from "./DeviceTable";

import useDataApi from "./Fetch";

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
    const [{ data, isLoading, isError }] = useDataApi(`/backend/device_state/${props.device_id}`, {});

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

const Dashboard = () => <DeviceTable format_header={TableHeader} format_row={TableRow}/>;

export default Dashboard;
