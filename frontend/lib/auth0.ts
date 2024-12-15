'use server'

import { Auth0Client } from "@auth0/nextjs-auth0/server"
import { User } from "@auth0/nextjs-auth0/types";


console.log("BACKEND_INTERNAL_API_URL:", process.env.BACKEND_INTERNAL_API_URL);
console.log("AUTH0_DOMAIN:", process.env.AUTH0_DOMAIN);
console.log("AUTH0_CLIENT_ID:", process.env.AUTH0_CLIENT_ID);
console.log("AUTH0_CLIENT_SECRET:", process.env.AUTH0_CLIENT_SECRET);
console.log("AUTH0_SECRET:", process.env.AUTH0_SECRET);
console.log("APP_BASE_URL:", process.env.APP_BASE_URL);



export const auth0 = new Auth0Client(
    {
        authorizationParameters: {
            audience: process.env.AUTH0_AUDIENCE,
        },
        async beforeSessionSaved(session) {
            try {
                const backendBaseUrl = process.env.BACKEND_INTERNAL_API_URL;
                const storeUrl = new URL(backendBaseUrl + '/auth/store-auth0-session');
                const response = await fetch(storeUrl, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(session),
                });
                if (!response.ok) {
                    console.error('Server returned an error:', response);
                    throw new Error('Server returned an error.');
                }
                const result = await response.json();
                if (result.status !== 'ok') {
                    console.error('Server responded with data:', result);
                    throw new Error('Server returned not-okay status.');
                }
                console.log('Session data stored successfully:', result);
            } catch (error) {
                console.error('Error storing session data:', error);
            }
            const ret = {
                ...session,
                user: {
                    ...filterClaims(session.user),
                },
            };
            return ret;
        },
    }
);


const DEFAULT_ALLOWED_CLAIMS = [
    "sub",
    "name",
    "nickname",
    "given_name",
    "family_name",
    "picture",
    "email",
    "email_verified",
    "org_id",
];

function filterClaims(
    claims: User
): User {
    return Object.keys(claims).reduce(
        (
            acc: User,
            key
        ) => {
            if (DEFAULT_ALLOWED_CLAIMS.includes(key)) {
                acc[key] = claims[key];
            }
            return acc;
        }, {} as User);
}


function isValidUrl(url: string): boolean {
    try {
        new URL(url);
        return true;
    } catch (_) {
        return false;
    }
}
