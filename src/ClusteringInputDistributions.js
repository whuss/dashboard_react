import React from "react";

import { useParams } from "react-router-dom";

import Button from "react-bootstrap/Button";
import Col from "react-bootstrap/Col";
import Row from "react-bootstrap/Row";
import Container from "react-bootstrap/Container";

import DeviceTable from "./DeviceTable";

import { usePlot } from "./BokehPlot";
import { LoadingAnimation } from "./Toolbar";
import { downloadFile } from "./Fetch";

import { useDropdown, useFilter } from "./Toolbar";

const columns = [
    "key_press_count",
    "delete_press_count",
    "enter_press_count",
    "shift_press_count",
    "space_press_count",
    "press_pause_count",
    "pause_length",
    "keystroke_time",
    "press_to_press_time",
    "click_count",
    "double_click_count",
    "rotation_distance",
    "rotation_speed",
    "event_count",
    "gesture_distance",
    "gesture_speed",
    "gesture_deviation",
    "gesture_duration_seconds",
];

const bigSpinnerStyle = {
    width: "300px",
    height: "300px",
    verticalAlign: "middle",
    display: "table-cell",
    textAlign: "center",
};

function useClusteringToolbar(_transformation) {
    if (!_transformation) {
        _transformation = "none";
    }

    const [transformation, setTransformation] = useDropdown(_transformation, {
        values: ["none", "power transform"],
        label: "Transformation",
    });

    const [selectedColumns, setColumnFilter] = useFilter("", {values: columns, label: "Data filter:"});

    //const params = `/clustring/input_distributation/${transformation}`;

    const sensorToolbar = <>{setColumnFilter}{setTransformation}</>;

    function plot_parameters(device) {
        return {
            device: device,
            transformation: transformation,
        };
    }

    return [sensorToolbar, plot_parameters, selectedColumns];
}

const DistributionPlot = (props) => {
    const plot_name = "PlotClusteringInputDistribution";
    var plot_parameters = props.plot_parameters;
    plot_parameters.column = props.column;

    const [{ fields, isLoading, isError, errorMsg }, plot] = usePlot(plot_name, plot_parameters);

    return (
        <>
            <Col>
                <LoadingAnimation style={bigSpinnerStyle} isLoading={isLoading} isError={isError} errorMsg={errorMsg}>
                    {plot}
                </LoadingAnimation>
            </Col>
        </>
    );
};

function rowFactory(plot_parameters, selectedColumns) {
    const TableRow = (props) => {
        const device = props.device_id;
        const plot_name = "PlotClusteringInputDistribution";
        const file_name = `clustering_input_distribution_${props.device_id}.xlsx`;

        return (
            <>
                <td>
                    <Container fluid>
                        <Row>
                            {selectedColumns.map((column) => (
                                <DistributionPlot
                                    key={column}
                                    plot_parameters={plot_parameters(device)}
                                    column={column}
                                />
                            ))}
                        </Row>
                    </Container>
                </td>
                <td>
                    <Button onClick={() => downloadFile(plot_name, plot_parameters(device), file_name)}>
                        Download
                    </Button>
                </td>
            </>
        );
    };

    return TableRow;
}

const TableHeader = () => (
    <>
        <th>Input Data</th>
        <th>Download</th>
    </>
);

const ClusteringInputDistribution = (props) => {
    const { transformation } = useParams();
    const [tools, plot_parameters, selectedColumns] = useClusteringToolbar(transformation);
    const TableRow = rowFactory(plot_parameters, selectedColumns);

    return (
        <>
            <p>
                <b>Warning:</b> Plotting of the distributions can take a very long time.
            </p>
            <DeviceTable format_header={TableHeader} format_row={TableRow} toolbar={tools} devices={props.devices} />
        </>
    );
};

export default ClusteringInputDistribution;
