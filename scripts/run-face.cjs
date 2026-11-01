'use strict';
// Product binding only. Face behavior stays in the pinned application.
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const product=require('../product.json');
process.env.GAR_HARDWARE_DIR ||= path.join(root,product.hardware.simulation);
process.env.GAR_BIN_DIR ||= path.join(root,'build');
require('../sources/gar-my-friend/application/face.cjs');
