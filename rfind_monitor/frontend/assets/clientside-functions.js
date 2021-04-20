window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        update_plots: function (index, storeData) {
            if (index !== undefined) {
                console.log("Updating plot from timestamp "+storeData.times[0])
                const updatedSpec = [{y: [storeData.spec[storeData.spec.length-1]], x: [storeData.freqs]}, [0], storeData.freqs.length]
                const updatedWaterfall = [{z: [storeData.spec]}, [0], storeData.spec.length]
                return [updatedSpec, updatedWaterfall];
            } else {
                throw window.dash_clientside.PreventUpdate;
            }
        }
    }
});