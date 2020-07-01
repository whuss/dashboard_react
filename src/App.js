import React from "react";
import Container from "react-bootstrap/Container";
import Jumbotron from "react-bootstrap/Jumbotron";
import ReactDOM from "react-dom";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";

import AnalyticsConnection from "./AnalyticsConnection";
import AnalyticsGaze from "./AnalyticsGaze";
import AnalyticsKeyboard from "./AnalyticsKeyboard";
import AnalyticsKeypress from "./AnalyticsKeypress";
import AnalyticsMouse from "./AnalyticsMouse";
import AnalyticsPowerTimeline from "./AnalyticsPowerTimeline";
import AnalyticsScenes from "./AnalyticsScenes";
import AnalyticsSensor from "./AnalyticsSensor";
import AnalyticsSettings from "./AnalyticsSettings";
import "./App.css";
import Plot from "./BokehPlot";
import ClusteringFrequency from "./ClusteringFrequency";
import ClusteringInputDistributions from "./ClusteringInputDistributions";
import ClusteringScatterPlot from "./ClusteringScatterPlot";
import ClusteringTimeline from "./ClusteringTimeline";
import Dashboard from "./Dashboard";
import DeviceDetails from "./DeviceDetails";
import Navigation from "./Navigation";
import SwitchCycles from "./SwitchCycles";
import SystemErrors from "./SystemErrors";
import SystemLogs from "./SystemLogs";
import SystemRestarts from "./SystemRestarts";
import SystemStability from "./SystemStability";
import DeviceStatus from "./SystemDeviceStatus";
import { LoadingAnimation, useDevice } from "./Toolbar";

const Title = (props) => {
    const titleBar = document.getElementById("titlebar-root");
    return ReactDOM.createPortal(<h2>{props.title}</h2>, titleBar);
};

const NavPortal = (props) => {
    const titleBar = document.getElementById("navbar-root");
    return ReactDOM.createPortal(<Navigation />, titleBar);
};

const NavRoute = (props) => (
    <Route path={props.path}>
        <Title title={props.title} />
        {props.children}
    </Route>
);

const MainView = (props) => {
    const devices = props.devices;
    return (
        <Container fluid>
            {/* A <Switch> looks through its children <Route>s and
              renders the first one that matches the current URL. */}
            <Switch>
                <NavRoute path="/about" title="About">
                    <About />
                </NavRoute>
                <NavRoute
                    path={["/analytics/sensor/:device/:sensor/:sample_rate/:start_date/:end_date", "/analytics/sensor"]}
                    title="Analytics Sensor"
                >
                    <AnalyticsSensor devices={devices} />
                </NavRoute>
                <NavRoute path="/analytics/settings" title="Analytics Settings">
                    <AnalyticsSettings devices={devices} />
                </NavRoute>
                <NavRoute path="/analytics/scenes" title="Analytics Scenes">
                    <AnalyticsScenes devices={devices} />
                </NavRoute>
                <NavRoute path="/analytics/power" title="Analytics Power timeline">
                    <AnalyticsPowerTimeline devices={devices} />
                </NavRoute>
                <NavRoute path="/analytics/connection" title="Analytics Connection">
                    <AnalyticsConnection devices={devices} />
                </NavRoute>
                <NavRoute path="/analytics/keyboard" title="Analytics Keyboard">
                    <AnalyticsKeyboard devices={devices} />
                </NavRoute>
                <NavRoute path="/analytics/keypress" title="Analytics Keypress">
                    <AnalyticsKeypress devices={devices} />
                </NavRoute>
                <NavRoute path="/analytics/mouse" title="Analytics Mouse">
                    <AnalyticsMouse devices={devices} />
                </NavRoute>
                <NavRoute path="/analytics/gaze" title="Analytics Gaze">
                    <AnalyticsGaze devices={devices} />
                </NavRoute>
                <NavRoute path="/clustering/input_distributions" title="Clustering Input Distributions">
                    <ClusteringInputDistributions devices={devices} />
                </NavRoute>
                <NavRoute path="/clustering/scatter_plot" title="Clustering Scatter Plot">
                    <ClusteringScatterPlot devices={devices} />
                </NavRoute>
                <NavRoute path="/clustering/frequency" title="Daily Cluster Frequency">
                    <ClusteringFrequency devices={devices} />
                </NavRoute>
                <NavRoute path="/clustering/timeline" title="Daily Cluster Timeline">
                    <ClusteringTimeline devices={devices} />
                </NavRoute>
                <NavRoute path="/statistics/switch_cycles" title="Statistics On/Off Cycles">
                    <SwitchCycles devices={devices} />
                </NavRoute>
                <NavRoute path="/system/stability" title="System Stability">
                    <SystemStability devices={devices} />
                </NavRoute>
                <NavRoute path="/system/restarts" title="System Restarts">
                    <SystemRestarts devices={devices} />
                </NavRoute>
                <NavRoute path="/system/errors" title="System Errors">
                    <SystemErrors devices={devices} />
                </NavRoute>
                <NavRoute path="/system/device_status" title="Device Status">
                    <DeviceStatus devices={devices} />
                </NavRoute>
                <NavRoute path="/database_size" title="Database Size">
                    <Plot src="/backend/plot_database_size" />
                </NavRoute>
                <NavRoute
                    path={[
                        "/logs/:device/:duration/:log_level/:timestamp",
                        "/logs/:device/:duration/:log_level",
                        "/logs/:device/:duration",
                        "/logs/:device",
                        "/logs",
                    ]}
                    title="Logs"
                >
                    <SystemLogs devices={devices} />
                </NavRoute>
                <NavRoute path={["/device_details/:device", "/device_details"]} title="Device Details">
                    <DeviceDetails devices={devices} />
                </NavRoute>
                <NavRoute path="/" title="Field study fact sheet (work in progress)">
                    <Dashboard devices={devices} />
                </NavRoute>
            </Switch>
        </Container>
    );
};

const AppRouter = (props) => {
    const [devices, isLoading, isError] = useDevice();
    return (
        <Router>
            <NavPortal />
            <LoadingAnimation isLoading={isLoading} isError={isError}>
                <MainView devices={devices} />
            </LoadingAnimation>
        </Router>
    );
};

class Bezier extends React.PureComponent {
    constructor(props) {
      super(props);
  
      this.state = {
        // These are our 3 Bézier points, stored in state.
        startPoint: { x: 10, y: 10 },
        controlPoint: { x: 190, y: 100 },
        endPoint: { x: 10, y: 190 },
  
        // We keep track of which point is currently being
        // dragged. By default, no point is.
        draggingPointId: null,
      };
    }
  
    handleMouseDown(pointId) {
      this.setState({ draggingPointId: pointId });
    }
  
    handleMouseUp() {
      this.setState({ draggingPointId: null });
    }
  
    handleMouseMove({ clientX, clientY }) {
      const { viewBoxWidth, viewBoxHeight } = this.props;
      const { draggingPointId } = this.state;
  
      // If we're not currently dragging a point, this is
      // a no-op. Nothing needs to be done.
      if (!draggingPointId) {
        return;
      }
  
      // During render, we capture a reference to the SVG
      // we're drawing, and store it on the instance with
      // `this.node`.
      // If we were to `console.log(this.node)`, we'd see a
      // reference to the underlying HTML element.
      // eg. `<svg viewBox="0 0 250 250"
      const svgRect = this.node.getBoundingClientRect();
  
      /*
      Ok, this next bit requires some explanation.
  
      The SVG rect gives us the element's position relative
      to the viewport.
  
      The user's mouse position with `clientX` and `clientY`
      is also relative to the viewport.
  
      What we actually care about, though, is the cursor's
      position relative to the SVG itself.
  
      Let's use a diagram! Imagine if ⬁ is the user's cursor:
  
  
      ------------------------------------------------------
      | viewport            ______________                 |
      |                    |              |                |
      |                    |       ⬁      | <- SVG         |
      |                    |______________|                |
      |____________________________________________________|
  
      ^----------------------------^ This is the `clientX`;
                                     the distance between the
                                     viewport and the cursor.
  
      ^-------------------^          This is the `svgRect`
                                     `left` value. Distance
                                     between the viewport and
                                     the SVG's left edge.
  
                          ^--------^ This is the distance we
                                     care about; the distance
                                     between the SVG's left
                                     edge, and the cursor.
  
      We can get that value with subtraction!
      */
      const svgX = clientX - svgRect.left;
      const svgY = clientY - svgRect.top;
  
      /*
      The next problem is that our SVG has a different
      coordinate system: Our SVG's `viewBox` might be 250x250,
      while in terms of the screen real-estate it might
      actually take up 500x500 pixels!
  
      To solve for this, I used cross-multiplication. Here are
      the variables we need:
  
      - svgX            The value we just calculated. The
                        cursor's `x` position within the SVG.
  
      - viewBoxWidth    The width of the SVG's internal
                        coordinate system. Specified via
                        props to this component.
  
      - svgRect.width   The on-screen width of the DOM element
                        Returned from `getBoundingClientRect`.
  
      Armed with that data, we can cross-multiply as follows:
  
           svgX               viewBoxX (unknown)
      --------------    =    --------------------
       viewBoxWidth             svgRect.width
  
      The left side of this equation is in terms of the screen
      real-estate: our cursor might be 250px into a 500px-wide
      svg.
  
      The right side is the SVG's viewBox coordinate system.
      We're `X` pixels into a 250px-wide viewBox.
  
      When we re-arrange the formula to solve for `viewBoxX`,
      we wind up with:
      */
      const viewBoxX = svgX * viewBoxWidth / svgRect.width;
  
      // We do the same thing for the vertical direction:
      const viewBoxY = svgY * viewBoxHeight / svgRect.height;
  
      // Phew! That was a lot of stuff, but in the end we
      // wind up with the user's mouse position within the
      // SVG's viewBox, and can update React state so that it
      // re-renders in this new position!
      this.setState({
        [draggingPointId]: { x: viewBoxX, y: viewBoxY },
      });
    }
  
    render() {
      const { viewBoxWidth, viewBoxHeight } = this.props;
      const {
        startPoint,
        controlPoint,
        endPoint,
      } = this.state;
  
      // As we've seen before, the quadratic Bézier curve
      // involves moving to the starting point, and then
      // specifying the control and end points with `Q`
      const instructions = `
        M ${startPoint.x},${startPoint.y}
        Q ${controlPoint.x},${controlPoint.y}
          ${endPoint.x},${endPoint.y}
      `;
  
      // While the Bézier curve is the main attraction,
      // we also have several shapes, including:
      //   - the handles for the start/control/end points
      //   - the dashed line that shows how the control
      //     point connects to the start/end points.
      return (
        <svg
          ref={node => (this.node = node)}
          viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`}
          onMouseMove={ev => this.handleMouseMove(ev)}
          onMouseUp={() => this.handleMouseUp()}
          onMouseLeave={() => this.handleMouseUp()}
          style={{
            overflow: 'visible',
            width: '100%',
            border: '1px solid',
          }}
        >
          <ConnectingLine
            from={startPoint}
            to={controlPoint}
          />
          <ConnectingLine from={controlPoint} to={endPoint} />
  
          <Curve instructions={instructions} />
  
          <LargeHandle
            coordinates={startPoint}
            onMouseDown={() =>
              this.handleMouseDown('startPoint')
            }
          />
  
          <LargeHandle
            coordinates={endPoint}
            onMouseDown={() =>
              this.handleMouseDown('endPoint')
            }
          />
  
          <SmallHandle
            coordinates={controlPoint}
            onMouseDown={() =>
              this.handleMouseDown('controlPoint')
            }
          />
        </svg>
      );
    }
  }
  
  // These helper stateless-functional-components allow us
  // to reuse styles, and give each shape a meaningful name.
  
  const ConnectingLine = ({ from, to }) => (
    <line
      x1={from.x}
      y1={from.y}
      x2={to.x}
      y2={to.y}
      stroke="rgb(200, 200, 200)"
      strokeDasharray="5,5"
      strokeWidth={2}
    />
  );
  
  const Curve = ({ instructions }) => (
    <path
      d={instructions}
      fill="none"
      stroke="rgb(213, 0, 249)"
      strokeWidth={1}
    />
  );
  
  const LargeHandle = ({ coordinates, onMouseDown }) => (
    <ellipse className="large_handle"
      cx={coordinates.x}
      cy={coordinates.y}
      rx={15}
      ry={15}
      onMouseDown={onMouseDown}
    />
  );
  
  const SmallHandle = ({ coordinates, onMouseDown }) => (
    <ellipse className="small_handle"
      cx={coordinates.x}
      cy={coordinates.y}
      rx={8}
      ry={8}
      onMouseDown={onMouseDown}
    />
  );

const About = (props) => (
    <>
    <Jumbotron>
        <h1 className="header">Todo ...</h1>    
    </Jumbotron>
    <div style={{width: 500, height: 500}}>
    <Bezier viewBoxWidth={500} viewBoxHeight={500} />
    </div>
    </>
);

const App = () => <AppRouter />;

export default App;
export { MainView };
