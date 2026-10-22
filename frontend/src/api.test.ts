import {afterEach,describe,expect,it,vi} from 'vitest';

afterEach(()=>{vi.unstubAllGlobals();vi.resetModules()});

describe('CSRF errors',()=>{
  it('shows a session error for a non-JSON 403 response',async()=>{
    const {api}=await import('./api');
    vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:false,status:403,json:async()=>{throw new SyntaxError('HTML')}}));
    await expect(api('auth/me/')).rejects.toThrow('Не удалось проверить сессию');
  });
  it('refreshes the token on the next attempt after a rejected session',async()=>{
    const {api}=await import('./api');
    const fetchMock=vi.fn()
      .mockResolvedValueOnce({ok:true,json:async()=>({csrfToken:'old-token'})})
      .mockResolvedValueOnce({ok:false,status:403,json:async()=>({error:{details:'Обновите сессию'}})})
      .mockResolvedValueOnce({ok:true,json:async()=>({csrfToken:'new-token'})})
      .mockResolvedValueOnce({ok:true,status:200,json:async()=>({username:'demo_a'})});
    vi.stubGlobal('fetch',fetchMock);
    await expect(api('auth/login/','POST',{username:'demo_a',password:'synthetic'})).rejects.toThrow('Обновите сессию');
    await expect(api('auth/login/','POST',{username:'demo_a',password:'synthetic'})).resolves.toEqual({username:'demo_a'});
    expect(fetchMock).toHaveBeenCalledTimes(4);
    expect(fetchMock.mock.calls[3][1].headers['X-CSRFToken']).toBe('new-token');
  });
});
