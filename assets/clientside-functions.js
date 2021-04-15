window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        update_plots: function (index, storeData) {
            const updatedSpec = [{y: [storeData.spec[storeData.spec.length-1]], x: [storeData.freqs]}, [0], storeData.freqs.length]
            const updatedWaterfall = [{z: [storeData.spec]}, [0], storeData.spec.length]
            return [updatedSpec, updatedWaterfall];
        }
    }
});