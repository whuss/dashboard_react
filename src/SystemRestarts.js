import React from "react";

import useDataApi from "./Fetch";

import { LoadingAnimation } from "./Toolbar";

import DeviceTable from "./DeviceTable";

function Restarts(props) {
    const [{ data, isLoading, isError }] = useDataApi(`/backend/system_restarts/${props.device}`, []);

    const restartTable = <div dangerouslySetInnerHTML={{ __html: data.table}}/>;
    return <LoadingAnimation isLoading={isLoading} isError={isError}>{restartTable}</LoadingAnimation>;
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

const SystemRestarts = () => <DeviceTable format_header={TableHeader} format_row={TableRow} />;

export default SystemRestarts;
