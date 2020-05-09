import React from "react";

import Button from "react-bootstrap/Button";

import DeviceTable from "./DeviceTable";

import Plot from "./BokehPlot";

function plotUrl(device) {
    return `/backend/plot_system_errors/${device}`;
}

const TableHeader = () => (
    <>
        <th>Total errors</th>
        <th>Error locations</th>
        <th>Download</th>
    </>
);

const TableRow = (props) => {
    return (
        <>
            <td></td>
            <td>
                <Plot src={plotUrl(props.device_id)} />
            </td>
            <td>
                <Button>Download</Button>
            </td>
        </>
    );
};

const SystemErrors = () => <DeviceTable format_header={TableHeader} format_row={TableRow} />;

export default SystemErrors;
