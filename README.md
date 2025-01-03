## Mockup API

### Usage

1. Install dependencies

```bash
docker build -t mockup-api .
```

2. Run the image

```bash
docker run -p 8000:8000 mockup-api
```

3. Send a request to the server

```bash
curl -X POST -H "Content-Type: application/json" -d '{"image_url": "https://getalign.astro-dev.tech/opengraph-image.png"}' http://localhost:8000/generate-mockup
```

### Known Issues

- Image resizing is not working properly
![Example request](https://github.com/user-attachments/assets/ac1dbea9-38bb-4601-bdda-7a270f3d738a)


### Future Improvements/TODO
- [ ] Upload the generated mockup directly to Azure Blob Storage.
- [ ] Test and improve error handling and logging (if needed).