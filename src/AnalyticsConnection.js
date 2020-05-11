import React from "react";

import Button from "react-bootstrap/Button";

import Plot from "./BokehPlot";
import DeviceTable from "./DeviceTable";
import { downloadFile } from "./Fetch";

function plotUrl(device) {
    return `/backend/plot_analytics_connection/${device}`;
}

const TableHeader = () => (
    <>
        <th>Cycles</th>
        <th>Download</th>
    </>
);

const TableRow = (props) => {
    return (
        <>
            <td>
                <Plot src={plotUrl(props.device_id)} />
            </td>
            <td>
                <Button onClick={() => downloadFile('PlotConnection', {device: props.device_id}, `analytics_connection_${props.device_id}.xlsx`)}>Download</Button>
            </td>
        </>
    );
};

const AnalyticsConnection = () => (
    <>
        <p>A data loss is detected when no data is received from the device for at least two minutes.</p>
        <p>
            Data from a day is excluded from analysis when either the downtime percentage is bigger than 5%, or the
            number of datalosses, i.e. the number of time intervals where the device has been offline, exceeds 5.
        </p>
        <p>
            <b>Note:</b> There is no connection data available for dates before 12.03.2020, these dates are always
            considered to have 0% downtime.
        </p>
        <DeviceTable format_header={TableHeader} format_row={TableRow} />;
    </>
);

export default AnalyticsConnection;
