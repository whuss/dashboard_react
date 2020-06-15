import React, { useState, useEffect } from "react";

import useDataApi from "./Fetch";

import { LoadingAnimation } from "./Toolbar";

import DeviceTable from "./DeviceTable";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faHeartbeat } from "@fortawesome/free-solid-svg-icons";

import PaginationBar from "./PaginationBar";

const RestartIcon = (props) => {
    const status = props.crash ? "SICK" : "HEALTHY";
    return (
        <div className={`icon ${status}`}>
            <FontAwesomeIcon icon={faHeartbeat} />
        </div>
    );
};

function Restarts(props) {
    const device = props.device;
    const [page, setPage ] = useState(1);
    const [{ data, isLoading, isError }, setUrl] = useDataApi(`/backend/system_restarts/${device}/${page}`, {});

    useEffect(() => {
        setUrl(`/backend/system_restarts/${device}/${page}`);
    }, [device, page, setUrl]);

    const restartTable = (
        <>
            {data && data.pagination &&
                <PaginationBar pagination={data.pagination} setPage={setPage} />
            }
            <table className="error-table">
                <thead>
                    <th>Time</th>
                    <th>IP Address</th>
                    <th>Commit</th>
                    <th>Branch</th>
                    <th>Version Timestamp</th>
                    <th>Crash</th>
                </thead>
                <tbody>
                    {data &&
                        data.table &&
                        data.table.map((row) => (
                            <tr>
                                <td>
                                    <a href={`/logs/${device}/5/TRACE/${row.timestamp}`}>{row.timestamp}</a>
                                </td>
                                <td>{row.ip}</td>
                                <td>{row.commit}</td>
                                <td>{row.branch}</td>
                                <td>{row.version_timestamp}</td>
                                <td>
                                    <RestartIcon crash={row.crash} />
                                </td>
                            </tr>
                        ))}
                </tbody>
            </table>
        </>
    );

    return (
        <LoadingAnimation isLoading={isLoading} isError={isError}>
            {restartTable}
        </LoadingAnimation>
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
            <td>
                <Restarts device={props.device_id} />
            </td>
        </>
    );
};

const SystemRestarts = (props) => (
    <DeviceTable format_header={TableHeader} format_row={TableRow} devices={props.devices} />
);

export default SystemRestarts;
