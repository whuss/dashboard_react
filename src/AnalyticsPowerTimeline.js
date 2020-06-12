import React from "react";

import Button from "react-bootstrap/Button";

import DeviceTable from "./DeviceTable";

import { usePlot } from "./BokehPlot";
import { LoadingAnimation, useDropdown } from "./Toolbar";
import { downloadFile } from "./Fetch";

function useToolbar(_color_scheme) {
    if (!_color_scheme) {
        _color_scheme = "power";
    }

    const [color_scheme, setColorScheme] = useDropdown(_color_scheme, {
        values: ["power", "gaze", "face_detected"],
        label: "Color Scheme",
    });

    const Toolbar = <>{setColorScheme}</>

    function plot_parameters(device) {
        return {
            device: device,
            color_scheme: color_scheme,
        };
    }

    return [Toolbar, plot_parameters];
}

function rowFactory(plot_parameters) {
    const TableRow = (props) => {
        const device = props.device_id;
        const plot_name = "PlotPowerTimeline";
        const file_name = `power_timeline_${device}.xlsx`;
        const [{ fields, isLoading, isError, errorMsg }, plot] = usePlot(plot_name, plot_parameters(device));

        return (
            <>
                <td>
                    <LoadingAnimation isLoading={isLoading} isError={isError} errorMsg={errorMsg}>
                        {plot}
                    </LoadingAnimation>
                </td>
                <td>
                    {!isLoading && !isError && (
                        <Button onClick={() => downloadFile(plot_name, plot_parameters(device), file_name)}>Download</Button>
                    )}
                </td>
            </>
        );
    };

    return TableRow;
}

const TableHeader = () => (
    <>
        <th>Cluster timeline</th>
        <th>Download</th>
    </>
);

const AnalyticsPowerTimeline = (props) => {
    const color_scheme = undefined;
    const [tools, plot_parameters] = useToolbar(color_scheme);
    const TableRow = rowFactory(plot_parameters);

    return (<DeviceTable format_header={TableHeader} format_row={TableRow} toolbar={tools} devices={props.devices}/>);
};

export default AnalyticsPowerTimeline;
