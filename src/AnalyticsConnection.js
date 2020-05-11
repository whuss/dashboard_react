import React from "react";

import Button from "react-bootstrap/Button";

import DeviceTable from "./DeviceTable";

import { usePlot } from "./BokehPlot";
import { LoadingAnimation } from "./Toolbar";
import { downloadFile } from "./Fetch";

const TableHeader = () => (
    <>
        <th>Cycles</th>
        <th>Download</th>
    </>
);

const TableRow = (props) => {
    const plot_name = "PlotConnection";
    const plot_parameters = { device: props.device_id };
    const file_name = `analytics_connection_${props.device_id}.xlsx`;
    const [{ fields, isLoading, isError, errorMsg }, plot] = usePlot(plot_name, plot_parameters);

    return (
        <>
            <td>
                <LoadingAnimation isLoading={isLoading} isError={isError} errorMsg={errorMsg}>
                    {plot}
                </LoadingAnimation>
            </td>
            <td>
                <Button onClick={() => downloadFile(plot_name, plot_parameters, file_name)}>Download</Button>
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
