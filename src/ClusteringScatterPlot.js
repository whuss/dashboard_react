import React from "react";

import { useParams } from "react-router-dom";

import Table from "react-bootstrap/Table";
import Button from "react-bootstrap/Button";
import Col from "react-bootstrap/Col";
import Row from "react-bootstrap/Row";
import Container from "react-bootstrap/Container";

import DeviceTable from "./DeviceTable";

import Plot from "./BokehPlot";

import { usePlot } from "./BokehPlot";
import { LoadingAnimation } from "./Toolbar";
import { downloadFile } from "./Fetch";

import { useDropdown } from "./Toolbar";

import Spinner from "react-bootstrap/Spinner";

const columns = [];

const bigSpinnerStyle = {
    width: "300px",
    height: "300px",
    verticalAlign: "middle",
    display: "table-cell",
    textAlign: "center",
};

const BigSpinner = (props) => (
    <div style={bigSpinnerStyle}>
        <Spinner animation="border" size="sm" variant="secondary" />
    </div>
);

function useClusteringToolbar(_dimension, _sampleSize) {
    if (!_dimension) {
        _dimension = 4;
    }

    if (!_sampleSize) {
        _sampleSize = 5000;
    }

    const [plotDimensions, setPlotDimensions] = useDropdown(_dimension, {
        values: [2, 3, 4, 5, 6],
        label: "Dimensions",
    });

    const [sampleSize, setSampleSize] = useDropdown(_sampleSize, {
        values: [5000, 2500, 1000, 500, 100, "ALL"],
        label: "Sample size",
    });

    //const params = `/clustring/input_distributation/${transformation}`;

    const sensorToolbar = <>{setPlotDimensions}{setSampleSize}</>;

    function plot_parameters(device) {
        return {
            device: device,
            sample_size: sampleSize,
            dimensions: plotDimensions,
        };
    }

    return [sensorToolbar, plot_parameters];
}

const ScatterPlot = (props) => {
    const plot_name = props.plot_name;
    const x_axis = props.x_axis;
    const y_axis = props.y_axis;
    var plot_parameters = props.plot_parameters;
    plot_parameters.x_axis = `d_${x_axis}`;
    plot_parameters.y_axis = `d_${y_axis}`;
    delete plot_parameters.dimensions;

    const [{ fields, isLoading, isError, errorMsg }, plot] = usePlot(plot_name, plot_parameters);

    return (
        <>
            <td>
                {(y_axis >= x_axis) ? <LoadingAnimation style={bigSpinnerStyle} isLoading={isLoading} isError={isError} errorMsg={errorMsg}>
                    {plot}
                </LoadingAnimation> : <></>}
            </td>
        </>
    );
};

function rowFactory(plot_parameters) {
    const TableRow = (props) => {
        const device = props.device_id;
        const plot_name = "PlotClusteringScatterPlot";
        const file_name = `clustering_scatter_plot_${props.device_id}.xlsx`;

        const local_plot_parameters = plot_parameters(device);
        local_plot_parameters.x_axis = "d_0";
        local_plot_parameters.y_axis = "d_0";
        
        const dimensions = local_plot_parameters.dimensions;
        delete local_plot_parameters.dimensions;

        //const rows = [...Array(dimensions).keys()].map((x) => `d_${x}`);
        const rows = [...Array(dimensions).keys()];

        const [{ fields, isLoading, isError, errorMsg }, plot] = usePlot(plot_name, local_plot_parameters);

        function drawRow(y_axis) {
            const rowElement = rows.map((x_axis) => (
                
                    <ScatterPlot
                        plot_name={plot_name}
                        plot_parameters={plot_parameters(device)}
                        x_axis={x_axis}
                        y_axis={y_axis}
                    />
            ));
            return (<tr>{rowElement}</tr>)
        }

        const tableStyle = {
            tableLayout: "fixed",
            width: `${300 * dimensions}px`,
            border: "none",
            padding: 0,
        };

        return (
            <>
                <td>{fields && fields.data_points}</td>
                <td>{fields && fields.significant_dimensions}</td>
                <td>
                    {/* <Table className="mpl-table" style={tableStyle}><tbody>{rows.map((y_axis) => drawRow(y_axis))}</tbody></Table> */}
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
        <th>Data points</th>
        <th>PCA Dimensions</th>
        <th>Cluster scatter plot</th>
        <th>Download</th>
    </>
);

const ClusteringScatterPlot = (props) => {
    const { dimension, sampleSize } = useParams();
    const [tools, plot_parameters] = useClusteringToolbar(dimension, sampleSize);
    const TableRow = rowFactory(plot_parameters);

    return (
        <>
            <p>
                <b>Warning:</b> Plotting of the distributions can take a very long time.
            </p>
            <DeviceTable format_header={TableHeader} format_row={TableRow} toolbar={tools} devices={props.devices} />
        </>
    );
};

export default ClusteringScatterPlot;
