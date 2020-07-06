import React from "react";
import { createPortal } from "react-dom";
import { render } from "@testing-library/react";
import App, { MainView } from "./App";
import { MemoryRouter } from "react-router-dom";
import { useDevice, LoadingAnimation } from "./framework/Toolbar";

jest.mock("react-dom");

const RouteTest = () => {
    const [devices, isLoading, isError] = useDevice();

    return (
        <LoadingAnimation isLoading={isLoading} isError={isError}>
            <MainView devices={devices} />
        </LoadingAnimation>
    );
};

test("analytics/connection", () => {
    render(
        <MemoryRouter initialEntries={["/analytics/connection"]}>
            <RouteTest />
        </MemoryRouter>
    );
});
