import React from "react";

import { usePlot } from "../BokehPlot";
import { LoadingAnimation } from "../Toolbar";

const Plot = () => {
    const plot_name = "PlotExampleBokeh";
    const plot_parameters = {number_of_points: 100};
    const { flags, plot } = usePlot(plot_name, plot_parameters, false);
    const { fields, isLoading, isError, errorMsg } = flags;

    return (
        <LoadingAnimation isLoading={isLoading} isError={isError} errorMsg={errorMsg}>
            {plot}
        </LoadingAnimation>
    )
};

export default Plot;