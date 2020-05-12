import React from "react";

import DeviceTable from "./DeviceTable";

import useDataApi from "./Fetch";

import { LoadingAnimation } from "./Toolbar";

const TableRow = (props) => {
    const [{ data, isLoading, isError }] = useDataApi(`/backend/device_state/${props.device_id}`, {});

    return (
        <>
            <td>
                <div className={`deviceMode ${data.study_mode}`}>{data.study_mode}</div>
            </td>
            <td>{data.offline_duration}</td>
            <td>
                <LoadingAnimation isLoading={isLoading} isError={isError}><i className={"fa fa-heartbeat " + data.health_status}></i></LoadingAnimation>
            </td>
            <td>{data.sick_reason}</td>
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

const Dashboard = (props) => <DeviceTable format_header={TableHeader} format_row={TableRow} devices={props.devices}/>;

export default Dashboard;
