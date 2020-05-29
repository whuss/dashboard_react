import React, { useEffect, useState } from "react";
import PropTypes, { InferProps } from "prop-types";

import Table from "react-bootstrap/Table";
import Col from "react-bootstrap/Col";

import Toolbar, { useDeviceFilter } from "./Toolbar";

import { useParams, Link } from "react-router-dom";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSortDown, faSortUp } from "@fortawesome/free-solid-svg-icons";

const DrawTable = (props) => {
    const [ascending, setAscenting] = useState(DrawTable.ascending);

    function sort(d: string[]) {
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

    const devices: string[] = props.devices.sort();

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
                        <th>
                            <Link className="device_link" to={`/device_details/${device}`}>
                                {device}
                            </Link>
                        </th>
                        <props.format_row device_id={device} />
                    </tr>
                ))}
            </tbody>
        </Table>
    );
};
DrawTable.ascending = true;

function DeviceTable({ devices, toolbar, format_header, format_row }: InferProps<typeof DeviceTable.propTypes>) {
    const { device }: { device: string } = useParams();
    const [selectedDevices, setFilterStr] = useDeviceFilter(device, devices);

    return (
        <>
            <Toolbar>
                {setFilterStr}
                {toolbar && toolbar}
            </Toolbar>
            <DrawTable devices={selectedDevices} format_header={format_header} format_row={format_row} />
        </>
    );
}

DeviceTable.propTypes = {
    devices: PropTypes.array.isRequired,
    toolbar: PropTypes.any,
    format_header: PropTypes.any.isRequired,
    format_row: PropTypes.any.isRequired,
};

export default DeviceTable;
