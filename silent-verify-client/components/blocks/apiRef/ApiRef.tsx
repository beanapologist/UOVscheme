"use client";

import { useRef } from "react";
import SwaggerUI from "swagger-ui-react";
import "swagger-ui-react/swagger-ui.css";

export default function Swagger({ url }: { url: string }) {
    const swaggerRef = useRef(null);
    return (
        <SwaggerUI
            url={url}
            deepLinking={true}
            persistAuthorization={true}
            docExpansion="list"
            tryItOutEnabled={true}
            defaultModelsExpandDepth={0}
            displayRequestDuration={true}
            onComplete={(system) => {
                swaggerRef.current = system;
            }}
        />
    );
}
