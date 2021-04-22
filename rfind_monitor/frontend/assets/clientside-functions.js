window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        update_plots: function (userClientStore) {
            if (index !== undefined) {
                console.log("Updating plot from timestamp "+userClientStore.timestamp)
                const updatedSpec = [{y: [userClientStore.spec[userClientStore.spec.length-1]], x: [userClientStore.freqs]}, [0], userClientStore.freqs.length]
                const updatedWaterfall = [{z: [userClientStore.spec]}, [0], userClientStore.spec.length]
                return [updatedSpec, updatedWaterfall];
            } else {
                throw window.dash_clientside.PreventUpdate;
            }
        }
    }
});