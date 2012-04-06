## Geologic Maps
### Collection: `/gm/`
- GET: Return a list of available geologic maps
	- acceptable formats: *text/html*
- POST: Create a new geologic map
	- post data: *multipart/form-data*
		- name: *any unused string*
		- title: *any string*
		- db: *a valid, NCGMP09-formatted ESRI file geodatabase*
		- map_type: *one of:* `Direct observation, Compilation`
		- (optional) metadata_url: *valid URL*
		
### Resource: `/gm/{gmId}/`
- GET: Return a represenation of a particular geologic map
	- acceptable formats: *text/html*
- PUT: *Not Implemented*
- DELETE: *Not Implemented*

### Resource Attributes: `/gm/{gmId}/{gmAttribute}`
- GET: *Not Implemented*
- PUT: Update the value of a particular attribute of a particular geologic map
	- valid gmAttributes:
		- title: *any string*
		- is_loaded: *true or false*. Toggling this attribute from `false` to `true` will result in the data from the geodatabase being loaded
		- metadata_url: *valid URL*
		
## Map Unit Descriptions, scoped to a particular geologic map
### Collection: `/gm/{gmId}/dmu/`
- GET: 
- POST: *Not Implemented*

### Resource: `/gm/{gmId}/dmu/{dmuId}/`
- GET:
- PUT:

### Attribute: `/gm/{gmId}/dmu/{dmuId}/{dmuAttribute}/`
- GET:
- PUT:

## Lithology Descriptions, scoped to a particular map unit description
### Collection: `/gm/{gmId}/dmu/{dmuId}/lith/`
- GET:
- POST:

### Resource: `/gm/{gmId}/dmu/{dmuId}/lith/{lithId}/`
- GET:
- PUT: 
- DELETE:

### Attribute: `/gm/{gmId}/dmu/{dmuId}/lith/{lithId}/{lithAttribute}/`
- GET:
- PUT:

## Geologic History of a particular map unit description
### Collection: `/gm/{gmId}/dmu/{dmuId}/age/`
- GET:
- POST:

### Resource: `/gm/{gmId}/dmu/{dmuId}/age/{ageId}/`
- GET:
- PUT:
- DELETE:

### Attribute: `/gm/{gmId}/dmu/{dmuId}/age/{ageId}/{ageAttribute}/`
- GET:
- PUT:

## Preferred Age of a particular map unit description
### Collection: `/gm/{gmId}/dmu/{dmuId}/preferredage/`
- GET:
- PUT:

### Resource: `/gm/{gmId}/dmu/{dmuId}/preferredage/{preferredageId}/`
- GET:
- PUT:
- DELETE:

### Attribute: `/gm/{gmId}/dmu/{dmuId}/preferredage/{preferredageId}/{preferredageAttribute}/`
- GET:
- PUT:

## Representative Values for a particular map unit description
### Collection: `/gm/{gmId}/dmu/{dmuId}/rep/`
- GET:
- POST:

### Resource: `/gm/{gmId}/dmu/{dmuId}/rep/{repId}/`
- GET:
- PUT: *Not Implemented*
- DELETE: *Not Implemented*

### Attribute: `/gm/{gmId}/dmu/{dmuId}/rep/{repId}/{repAttribute}/`
- GET:
- PUT:

