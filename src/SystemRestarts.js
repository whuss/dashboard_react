import React from "react";

import useDataApi from "./Fetch";

import Spinner from "react-bootstrap/Spinner";

import DeviceTable from "./DeviceTable";

function Restarts(props) {
    const [{ data, isLoading, isError }] = useDataApi(`/backend/system_restarts/${props.device}`, []);

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

const SystemRestarts = () => <DeviceTable format_header={TableHeader} format_row={TableRow} />;

export default SystemRestarts;
