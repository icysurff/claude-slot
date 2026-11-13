export default {
	providerName: 'sample_provider',
	gameName: 'wild_respin_5x4',
	gameID: '0_0_wildrespin',
	rtp: 0.965,
	numReels: 5,
	numRows: [4, 4, 4, 4, 4],
	betModes: {
		base: {
			cost: 1.0,
			feature: true,
			buyBonus: false,
			rtp: 0.965,
			max_win: 50000,
		},
		enhancer: { cost: 1.5, feature: true, buyBonus: false, rtp: 0.965, max_win: 50000 },
		buy_normal: { cost: 31, feature: false, buyBonus: true, rtp: 0.965, max_win: 50000 },
		buy_super: { cost: 104, feature: false, buyBonus: true, rtp: 0.965, max_win: 50000 },
		buy_jackpot: { cost: 1700, feature: false, buyBonus: true, rtp: 0.965, max_win: 50000 },
		buy_wildreels: { cost: 2600, feature: false, buyBonus: true, rtp: 0.965, max_win: 50000 },
	},
	symbols: {
 "W": {
  "paytable": null,
  "special_properties": [
   "wild"
  ]
 },
 "S": {
  "paytable": null,
  "special_properties": [
   "scatter"
  ]
 },
 "H1": {
  "paytable": [
   {
    "5": 20.0
   },
   {
    "4": 5.0
   },
   {
    "3": 2.5
   }
  ]
 },
 "H2": {
  "paytable": [
   {
    "5": 12.0
   },
   {
    "4": 3.0
   },
   {
    "3": 1.5
   }
  ]
 },
 "H3": {
  "paytable": [
   {
    "5": 6.0
   },
   {
    "4": 2.0
   },
   {
    "3": 1.0
   }
  ]
 },
 "H4": {
  "paytable": [
   {
    "5": 4.0
   },
   {
    "4": 1.2
   },
   {
    "3": 0.6
   }
  ]
 },
 "H5": {
  "paytable": [
   {
    "5": 2.5
   },
   {
    "4": 0.8
   },
   {
    "3": 0.4
   }
  ]
 },
 "L1": {
  "paytable": [
   {
    "5": 1.2
   },
   {
    "4": 0.5
   },
   {
    "3": 0.3
   }
  ]
 },
 "L2": {
  "paytable": [
   {
    "5": 0.8
   },
   {
    "4": 0.4
   },
   {
    "3": 0.2
   }
  ]
 },
 "L3": {
  "paytable": [
   {
    "5": 0.6
   },
   {
    "4": 0.3
   },
   {
    "3": 0.2
   }
  ]
 },
 "L4": {
  "paytable": [
   {
    "5": 0.5
   },
   {
    "4": 0.3
   },
   {
    "3": 0.1
   }
  ]
 },
 "L5": {
  "paytable": [
   {
    "5": 0.3
   },
   {
    "4": 0.2
   },
   {
    "3": 0.1
   }
  ]
 },
 "L6": {
  "paytable": [
   {
    "5": 0.3
   },
   {
    "4": 0.2
   },
   {
    "3": 0.1
   }
  ]
 },
 "L7": {
  "paytable": [
   {
    "5": 0.2
   },
   {
    "4": 0.1
   },
   {
    "3": 0.1
   }
  ]
 },
 "L8": {
  "paytable": [
   {
    "5": 0.2
   },
   {
    "4": 0.1
   },
   {
    "3": 0.1
   }
  ]
 }
},
	paddingReels: {
		basegame: '',
		freegame: '',
	},
} as const;
