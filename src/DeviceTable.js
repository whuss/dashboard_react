import React, { useEffect, useState } from "react";

import Table from "react-bootstrap/Table";
import Col from 'react-bootstrap/Col';

import Toolbar, { useDeviceFilter } from "./Toolbar";

import { useParams, Link } from "react-router-dom";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSortDown, faSortUp } from "@fortawesome/free-solid-svg-icons";

const DrawTable = (props) => {
    const [ascending, setAscenting] = useState(DrawTable.ascending);

    function sort(d) {
        if (!ascending) {
            return d.reverse();
        }
        return d;
    }

    const SortIcon = () => {
        if (ascending) {
            return <FontAwesomeIcon icon={faSortDown} />;
        }
        return <FontAwesomeIcon icon={faSortUp} />;
    };

    const devices = props.devices.sort();

    useEffect(() => {
        console.log("Set sorting: ", ascending);
        DrawTable.ascending = ascending;
    }, [ascending]);

    return (
        <Table className={"dataTable"} hover>
            <thead>
                <tr>
                    <th id="head_device" onClick={() => setAscenting(!ascending)}>
                        Device <SortIcon />
                    </th>
                    <props.format_header />
                </tr>
            </thead>
            <tbody>
                {sort(devices).map((device) => (
                    <tr key={device}>
                        <th><Link className="device_link" to={`/device_details/${device}`}>{device}</Link></th>
                        <props.format_row device_id={device} />
                    </tr>
                ))}
            </tbody>
        </Table>
    );
};
DrawTable.ascending = true;

function DeviceTable(props) {
    let params = useParams()
    const [selectedDevices, setFilterStr] = useDeviceFilter(params.device, props.devices);

    return (
        <>
            <Toolbar>
                {setFilterStr}
                {props.toolbar && props.toolbar}
            </Toolbar>
            <DrawTable devices={selectedDevices} format_header={props.format_header} format_row={props.format_row} />
        </>
    );
}

export default DeviceTable;
